---
id: kotlin-135
title: "launch vs async: When to Use Each / launch против async: когда использовать"
aliases: ["launch vs async: When to Use Each", "launch против async: когда использовать"]

# Classification
topic: kotlin
subtopics: [coroutines, patterns]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140027

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-coroutine-context-elements--kotlin--hard, q-kotlin-multiplatform-overview--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-10

tags: [coroutines, difficulty/easy, kotlin]
date created: Sunday, October 12th 2025, 3:39:12 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140027

# Question (EN)
> Kotlin Coroutines advanced topic 140027

## Ответ (RU)

`launch` и `async` оба являются coroutine builders, но различаются способом работы с результатами и обработкой исключений.

### Launch
Стиль "запустить и не ждать результата" для побочных эффектов, возвращает `Job`:
```kotlin
val job = launch {
    delay(1000)
    println("Task completed")
}
job.join()  // Явно ждем завершения, если нужно
```
- Если не вызвать `join()` или не сохранить `Job`, корутина выполнится в своем scope, а необработанные исключения будут репортиться через механизм обработки исключений корутин (например, в scope или глобальный handler).

### Async
Возвращает `Deferred<T>` для вычисления значения:
```kotlin
val deferred = async {
    delay(1000)
    "Result"
}
val result = deferred.await()  // Получить результат (или исключение)
println(result)  // "Result"
```
- `async` следует использовать, когда вы рассчитываете получить значение и обязательно вызывать `await()` (или иным образом потребить `Deferred`); использовать `async` как "fire-and-forget" без `await()` считается антипаттерном.

### Ключевые Отличия
| Функция | launch | async |
|---------|--------|-------|
| Возвращает | `Job` | `Deferred<T>` |
| Результат | Нет значения (для вызова) | Значение типа `T` |
| Основное использование | Побочные эффекты | Параллельные вычисления значения |
| Исключения | Пробрасываются в `CoroutineExceptionHandler`/родительский scope при завершении, нет значения для чтения | Исключение откладывается до `await()`: при вызове `await()` оно будет выброшено (и также участвует в иерархии Job'ов) |

### Выбор Между Ними
```kotlin
// Используйте launch для побочных эффектов
launch {
    saveToDatabase(data)
}

// Используйте async для получения результата
val result = async {
    fetchFromApi()
}.await()

// Параллельные async-вычисления
val r1 = async { fetch1() }
val r2 = async { fetch2() }
combine(r1.await(), r2.await())
```

См. также: [[c-kotlin]], [[c-coroutines]], [[c-kotlin-coroutines-basics]]

## Answer (EN)

`launch` and `async` are both coroutine builders but differ in how they work with results and exceptions.

### Launch
"Fire-and-don't-wait-for-a-value" style for side effects, returns a `Job`:
```kotlin
val job = launch {
    delay(1000)
    println("Task completed")
}
job.join()  // Explicitly wait for completion when needed
```
- If you don't call `join()` or keep the `Job`, the coroutine will run in its scope; unhandled exceptions are reported via the coroutine exception mechanism (e.g., scope or global handler).

### Async
Returns a `Deferred<T>` for computing a value:
```kotlin
val deferred = async {
    delay(1000)
    "Result"
}
val result = deferred.await()  // Get result (or exception)
println(result)  // "Result"
```
- `async` should be used when you intend to produce a value and you must call `await()` (or otherwise consume the `Deferred`); using `async` as fire-and-forget without `await()` is considered an anti-pattern.

### Key Differences
| Feature | launch | async |
|---------|--------|-------|
| Returns | `Job` | `Deferred<T>` |
| Result | No value (for caller) | Value of type `T` |
| Usage | Side effects | Concurrent value computations |
| Exception | Propagated to `CoroutineExceptionHandler`/parent scope on completion; no value to read | Stored and rethrown when `await()` is called (also participates in the Job hierarchy) |

### Choosing Between Them
```kotlin
// Use launch for side effects
launch {
    saveToDatabase(data)
}

// Use async for results
val result = async {
    fetchFromApi()
}.await()

// Parallel async computations
val r1 = async { fetch1() }
val r2 = async { fetch2() }
combine(r1.await(), r2.await())
```

See also: [[c-kotlin]], [[c-coroutines]], [[c-kotlin-coroutines-basics]]

## Дополнительные Вопросы (RU)

1. Когда уместно использовать `launch` внутри `supervisorScope` и как это влияет на обработку исключений?
2. В каких случаях вы предпочтете несколько `async` с `awaitAll` вместо последовательного вызова `suspend`-функций?
3. Как неправильно использованный `async` (без `await`) может привести к утечкам или "потерянным" исключениям?
4. Как выбрать `CoroutineDispatcher` при использовании `launch` и `async` для CPU-bound и IO-bound задач?
5. Как `structured concurrency` помогает правильно комбинировать `launch` и `async` в одном `CoroutineScope`?

## Follow-ups

1. When is it appropriate to use `launch` inside a `supervisorScope` and how does that affect exception handling?
2. In which cases would you prefer multiple `async` calls with `awaitAll` over sequential `suspend` calls?
3. How can improperly used `async` (without `await`) lead to leaks or "lost" exceptions?
4. How do you choose a `CoroutineDispatcher` when using `launch` and `async` for CPU-bound vs IO-bound work?
5. How does structured concurrency help you combine `launch` and `async` correctly within a single `CoroutineScope`?

## Ссылки (RU)

- [Документация по Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

## Related Questions

### Related (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Coroutines
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutines
- [[q-coroutine-scope-basics--kotlin--easy]] - Coroutines

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
