---\
id: kotlin-246
title: "What is Dispatchers.Unconfined and when to use it? / Dispatchers.Unconfined применение"
aliases: [Dispatchers Unconfined, Dispatchers.Unconfined применение]
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
question_kind: theory
status: draft
created: "2025-10-12"
updated: "2025-11-10"
tags: ["coroutines", "difficulty/medium", "dispatchers", "kotlin", "unconfined"]
description: "Comprehensive guide to What is Dispatchers.Unconfined and when to use it? in Kotlin coroutines"
moc: moc-kotlin
related: [c-coroutines, c-kotlin-coroutines-basics, q-coroutine-dispatchers--kotlin--medium]
subtopics: [coroutines, dispatchers]

---\
# Вопрос (RU)

> Что такое `Dispatchers.Unconfined` в корутинах Kotlin и когда его следует использовать?

# Question (EN)

> What is `Dispatchers.Unconfined` in Kotlin coroutines, and when should you use it?

## Ответ (RU)

Кратко:
- `Dispatchers.Unconfined` — специальный диспетчер из [[c-coroutines]], который:
  - Запускает корутину в текущем потоке/стеке вызова (без немедленного переключения контекста).
  - Не закрепляет выполнение за конкретным потоком после приостановки.
  - Возобновляет корутину в том потоке, который выбирает соответствующая `suspend`-функция.
- Основное назначение:
  - Низкоуровневый код библиотек/фреймворков корутин.
  - Сценарии, где вы полностью контролируете точки приостановки/возобновления и хотите избежать лишнего диспатча.
  - Некоторые тестовые/отладочные и демонстрационные сценарии.
- Это НЕ универсальный диспетчер и НЕ замена `Dispatchers.Main` / `Dispatchers.IO` / `Dispatchers.Default`.

Детали поведения:
- Старт:
  - `launch(Dispatchers.Unconfined) { ... }` начинает выполняться немедленно в текущем потоке до первой приостановки.
- После первой приостановки:
  - Поток возобновления определяется реализацией `suspend`-функции.
  - Пример: `delay(...)` возобновит выполнение в потоке своего планировщика, а не обязательно в исходном потоке.
- Нет гарантий:
  - Нет гарантии остаться в исходном потоке, фиксированном пуле или одном потоке между приостановками.
  - Нельзя использовать, если важна привязка к потоку (например, UI-поток, неперенесённые `ThreadLocal` и т.п.).

Сравнение со стандартными диспетчерами:
- `Dispatchers.Main`:
  - Гарантирует выполнение на главном/UI-потоке; безопасен для обновления UI.
  - `Dispatchers.Unconfined` таких гарантий не даёт, поэтому для UI опасен.
- `Dispatchers.IO`:
  - Пул потоков для блокирующих операций ввода-вывода.
- `Dispatchers.Default`:
  - Пул потоков для CPU-емких задач.
- `NewSingleThreadContext` / свои `Executor`-ы:
  - Гарантированная привязка к одному (или заданному набору) потоку.
- `Dispatchers.Unconfined`:
  - Не владеет потоками и не имеет собственного пула.
  - Сначала использует текущий контекст, затем следует за потоками, на которых возобновляют `suspend`-функции.

Пример поведения:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(Dispatchers.Unconfined) {
        println("Unconfined start: thread = ${Thread.currentThread().name}")
        delay(100)
        println("Unconfined after delay: thread = ${Thread.currentThread().name}")
    }

    launch {
        println("Default runBlocking context: thread = ${Thread.currentThread().name}")
    }
}
```

Типичный (но не гарантированный) результат:
- Первый `println` для `Dispatchers.Unconfined` — на потоке `runBlocking` (например, `main`).
- После `delay` — на другом потоке (например, `DefaultExecutor`).
- Вторая корутина без `Dispatchers.Unconfined` остаётся в контексте `runBlocking`.

Почему это опасно для UI:

```kotlin
// В Android или другой UI-среде
scope.launch(Dispatchers.Unconfined) {
    val result = repository.load()
    // После suspend мы можем оказаться не на UI-потоке
    textView.text = result // Потенциальный сбой или некорректное поведение
}
```

Это неправильно, потому что `Dispatchers.Unconfined` не гарантирует возврат на главный/UI-поток.
Правильный подход:

```kotlin
scope.launch(Dispatchers.Main) {
    val result = withContext(Dispatchers.IO) { repository.load() }
    textView.text = result
}
```

Когда (редко) можно использовать `Dispatchers.Unconfined`:
- В библиотечном/фреймворк-коде, когда:
  - Вы реализуете собственные операторы/билдеры корутин и контролируете используемые диспетчеры.
  - Вам важно избежать лишних переключений контекста, и корректность не зависит от конкретного потока.
- В демо/REPL/консольных примерах, чтобы показать механику из [[c-kotlin-coroutines-basics]] без усложнения выбором диспетчеров.
- В тестах:
  - Иногда вместе с тестовыми диспетчерами, хотя обычно предпочтительнее использовать средства `kotlinx.coroutines-test`.

Когда НЕ стоит использовать `Dispatchers.Unconfined`:
- В продакшен-коде приложения:
  - Для UI-логики и обновлений интерфейса.
  - Там, где есть зависимости от потока (`ThreadLocal`, небезопасное разделяемое состояние без синхронизации).
  - В сложных иерархиях структурированной конкуррентности, где нужны предсказуемые потоки.
- В качестве "дефолтного" диспетчера для бизнес-логики или I/O.

Краткий ответ для собеседования:
- `Dispatchers.Unconfined` запускает корутину в текущем потоке и после приостановок возобновляет её на том потоке, который выбирают `suspend`-функции. Он не привязан к конкретному потоку, что делает его непредсказуемым и потому почти всегда непригодным для прикладного/UI-кода. Предназначен в основном для низкоуровневых и тестовых сценариев.

## Answer (EN)

Key definition:
- `Dispatchers.Unconfined` is a special dispatcher from [[c-coroutines]] that:
  - Starts the coroutine in the current call frame/thread (no immediate dispatch).
  - Does not confine execution to any specific thread after suspension.
  - Resumes on whatever thread the corresponding `suspend` function decides to use.
- It is primarily intended for:
  - Very low-level coroutine library/framework code.
  - Situations where you fully control suspension/resumption and want to avoid unnecessary dispatch.
  - Some testing/debugging and demonstration scenarios.
- It is NOT a general-purpose dispatcher and NOT a replacement for `Dispatchers.Main` / `Dispatchers.IO` / `Dispatchers.Default`.

Behavior details:
- Starting:
  - `launch(Dispatchers.Unconfined) { ... }` starts executing immediately in the current thread until the first suspension point.
- After first suspension:
  - The resumption thread is determined by the `suspend` function.
  - Example: `delay(...)` resumes in its scheduler thread, not necessarily the original one.
- No guarantee:
  - There is no guarantee of staying on the caller thread, any specific pool, or a single thread.
  - Therefore it must not be used for code that relies on thread affinity (Android UI, Swing/JavaFX UI, raw `ThreadLocal` state, etc.).

Comparison to standard dispatchers:
- `Dispatchers.Main`:
  - Confined to the main/UI thread; safe for UI updates.
  - `Dispatchers.Unconfined` is not confined; UI with it is unsafe.
- `Dispatchers.IO`:
  - Shared pool optimized for blocking I/O.
- `Dispatchers.Default`:
  - Shared pool optimized for CPU-bound work.
- `NewSingleThreadContext` / dedicated executors:
  - Always run on their own thread(s) with stable affinity.
- `Dispatchers.Unconfined`:
  - Does not own threads or a pool.
  - Delegates to the current execution context initially, then to the threads used by `suspend` resumptions.

Code example (behavior demo):

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(Dispatchers.Unconfined) {
        println("Unconfined start: thread = ${Thread.currentThread().name}")
        delay(100)
        println("Unconfined after delay: thread = ${Thread.currentThread().name}")
    }

    launch {
        println("Default runBlocking context: thread = ${Thread.currentThread().name}")
    }
}
```

Typical (non-guaranteed) outcome:
- First log for `Dispatchers.Unconfined` is on the `runBlocking` thread (e.g., `main`).
- After `delay`, it resumes on a different thread (e.g., `DefaultExecutor`).
- The child without `Dispatchers.Unconfined` stays confined to `runBlocking`'s context.

Why this is dangerous for UI:

```kotlin
// On Android or any UI framework
scope.launch(Dispatchers.Unconfined) {
    val result = repository.load()
    // After suspension we may be on a background thread
    textView.text = result // Potential crash/violation of UI-thread rules
}
```

This is incorrect because `Dispatchers.Unconfined` does not ensure returning to the main/UI thread.
Use instead:

```kotlin
scope.launch(Dispatchers.Main) {
    val result = withContext(Dispatchers.IO) { repository.load() }
    textView.text = result
}
```

When (rarely) to use `Dispatchers.Unconfined`:
- In coroutine libraries/frameworks when:
  - You implement custom operators/builders and control which dispatchers are used for all `suspend` calls.
  - You want to avoid extra dispatch hops and correctness does not depend on a specific thread.
- In simple demos/REPL/console examples to illustrate mechanics from [[c-kotlin-coroutines-basics]] without dispatcher noise.
- In tests:
  - Occasionally with testing dispatchers, though `kotlinx.coroutines-test` utilities are usually preferred.

When NOT to use `Dispatchers.Unconfined`:
- In production application code for:
  - UI-related work.
  - Code relying on thread confinement (`ThreadLocal`, unsynchronized mutable shared state).
  - Structured concurrency hierarchies where predictable threading is important.
- As a default dispatcher for business logic or I/O.

`Short` interview-style summary:
- `Dispatchers.Unconfined` starts a coroutine in the current thread and resumes it on whatever thread each suspension uses. Because it is not confined to a specific thread, it is unpredictable and generally unsuitable for most application-level code, especially UI. It exists mainly for narrow low-level and testing scenarios where you fully understand and control dispatching.

## Follow-ups

1. What is the difference between `Dispatchers.Unconfined` and `Dispatchers.Main` in terms of thread confinement?
2. How does `Dispatchers.Unconfined` interact with `suspend` functions like `delay` or `withContext`?
3. Why is `Dispatchers.Unconfined` generally discouraged in production Android applications?
4. How would you demonstrate the behavior of `Dispatchers.Unconfined` in a small code sample?
5. In what kind of coroutine library/framework code could `Dispatchers.Unconfined` be appropriate?

## References

- "Coroutines" section in the official Kotlin documentation
- kotlinx.coroutines API reference for dispatchers
- Articles and guides discussing pitfalls and internals of `Dispatchers.Unconfined`

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]
