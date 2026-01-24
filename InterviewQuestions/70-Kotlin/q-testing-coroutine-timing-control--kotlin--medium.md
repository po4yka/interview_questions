---
anki_cards:
- slug: q-testing-coroutine-timing-control--kotlin--medium-0-en
  language: en
  anki_id: 1768326285207
  synced_at: '2026-01-23T17:03:50.976666'
- slug: q-testing-coroutine-timing-control--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326285231
  synced_at: '2026-01-23T17:03:50.978250'
---
## Answer (EN)

Testing time-dependent coroutine code without virtual time requires real delays, which makes tests slow, flaky, and non-deterministic. The `kotlinx-coroutines-test` module provides virtual time via `TestScope` and `TestDispatcher`, letting you explicitly and instantly control delayed and scheduled work.

All examples below assume `kotlinx-coroutines-test` 1.6+: virtual time is managed by the test scheduler and changes when you drive it using `advanceTimeBy`, `advanceUntilIdle`, `runCurrent`, or when `runTest` internally advances time while executing scheduled tasks. The `delay` call itself does not sleep real time.

### Virtual time Concept

- Virtual time lets you fast-forward coroutine delays without real waiting.
- `delay(1000)` only schedules continuation at time `1000`; until you move the virtual clock (or it is moved by the scheduler via test primitives), the coroutine does not resume.

### `TestScope` And `TestDispatcher`

- `runTest { ... }` creates a `TestScope` with a `TestDispatcher` (by default `StandardTestDispatcher`).
- All coroutines launched in this scope are controlled by the virtual-time scheduler.
- Pattern:
  - Use `delay` in the code under test.
  - In tests, call `advanceTimeBy` / `advanceUntilIdle` / `runCurrent` to drive execution instead of real sleeping.

### `advanceTimeBy(millis)` — Precise Stepwise Control

Use `advanceTimeBy` when you need fine-grained control and intermediate assertions.

Typical uses (matching RU examples):

- One-shot delay:
  - Launch a coroutine with `delay(1000)`.
  - Assert state before advancing.
  - `advanceTimeBy(500)` → still not completed.
  - `advanceTimeBy(500)` → completion observed at `currentTime == 1000`.
- Multiple delayed tasks:
  - Launch tasks with different delays (e.g., 100, 200, 300 ms).
  - Step the clock and assert which tasks have completed after each step.
- Debounce / rate limiting:
  - Model debounce by cancelling/relaunching a job with a delay.
  - Step time in segments to verify that only the last event is executed.
  - For rate-limiters, assert emitted timestamps (e.g., `0L, 1000L, 2000L`).

Key property: only tasks scheduled at or before the new virtual time are executed.

### `advanceUntilIdle()` — Run All Finite Work

Use `advanceUntilIdle()` when:

- All scheduled work (including recursively scheduled work) is finite.
- You want the system to reach quiescence without caring about the exact times between steps.

Scenarios:

- Several delayed tasks with different delays: `advanceUntilIdle()` runs them all and sets `currentTime` to the largest scheduled delay.
- Bounded repeated work with `repeat` and `delay`: `advanceUntilIdle()` drives it to completion.
- Dynamically scheduled work (recursive scheduling, producer-consumer with close): `advanceUntilIdle()` keeps jumping to the next event until no tasks remain.

Important: For infinite or open-ended loops, `advanceUntilIdle()` may never finish; in such cases, prefer bounded loops, manual `advanceTimeBy` steps, and explicit cancellation.

### `runCurrent()` — Only Tasks at Current time

Use `runCurrent()` to:

- Execute tasks scheduled at the current `currentTime` without moving the clock.
- Flush:
  - Immediate launches on the test dispatcher.
  - Continuations scheduled with `delay(0)`.

Examples:

- Launch immediate work and delayed work; `runCurrent()` runs only immediate work.
- Create more tasks at the same time; another `runCurrent()` flushes them, `currentTime` unchanged.

### `currentTime` — Observable Virtual Clock

- `currentTime` reflects the test scheduler clock in milliseconds.
- Use it to:
  - Assert when events happen relative to each other.
  - Store timestamps in domain events and verify ordering and spacing.

### Testing `delay()` Semantics

Use `advanceTimeBy`, `advanceUntilIdle`, and `runCurrent` to express clear expectations:

- For a `delay(1000)`, assert nothing happens before you advance; then advance in steps and verify exactly when execution continues.
- For loops with repeated `delay(100)`, advance in 100 ms increments and assert that each iteration has run.
- For `delay(0)`, verify that work is executed only after `runCurrent()` (since continuation is queued at the current time).

### Testing `withTimeout` / `withTimeoutOrNull`

Mirror RU examples:

- Success case:
  - `withTimeout(1000) { delay(500); "Success" }`.
  - `advanceTimeBy(500)` → `await()` returns "Success", `currentTime == 500`.
- Timeout case:
  - `withTimeout(1000) { delay(2000) }`.
  - `advanceTimeBy(1000)` → `await()` throws `TimeoutCancellationException`, `currentTime == 1000`.
- `withTimeoutOrNull`:
  - Shorter work: advance below timeout and expect result.
  - Longer work: advance to timeout and assert result is `null`.

### Testing Periodic Operations

You can deterministically verify periodic behavior:

- Polling loops with `delay(1000)`:
  - Repeatedly call `advanceTimeBy(1000)` and assert call counts and final `currentTime`.
- Ticker-like patterns:
  - Create a `ticker` bound to the test dispatcher; advance virtual time and assert ticks at `0, 1000, 2000, ...`.
- Repeating tasks with `repeat` + `delay`:
  - Use partial `advanceTimeBy` followed by `advanceUntilIdle()` to assert both timing and completion.

### Testing `Flow` Timing (`debounce`, `sample`, `onEach` delays)

Aligning with RU examples:

- `debounce`:
  - Emit values with short gaps and a longer gap.
  - `advanceUntilIdle()` and assert only the debounced values (e.g., `3` as last of the burst, `4` after a long pause).
- `sample`:
  - Emissions every 100 ms, `sample(250)`.
  - Sampling occurs at 0, 250, 500, 750, ... ms; on each tick the operator emits the latest value.
  - With that schedule, the collected values deterministically become `2, 4, 7, 9`.
- `onEach { delay(...) }`:
  - Collect and record `currentTime`; assert timestamps increase with expected steps.

### Testing `ViewModel` and `StateFlow`/`SharedFlow`

Parallel to RU `ViewModel` example:

- Expose UI state as `StateFlow`.
- Use `runTest` and the test dispatcher.
- In tests:
  - Start collecting from the flow (often via `backgroundScope`) so collection lives alongside the scenario.
  - Trigger `ViewModel` methods that use `delay`/timeouts/retries.
  - Drive virtual time with `advanceTimeBy` / `advanceUntilIdle`.
  - Assert the sequence and timing of states (e.g., Idle → Loading → Success/Error → retries).

### Deterministic race/ordering Tests

Use virtual time to remove nondeterminism:

- Launch multiple coroutines with different `delay` values.
- Advance in steps so they complete in a predictable order.
- "First successful" scenarios:
  - Start multiple async operations with different delays.
  - Advance until the earliest completion; cancel others and assert the correct winner.

### Common Pitfalls

Aligned with RU "Частые ошибки":

- Forgetting to advance time:
  - `delay` never completes without `advanceTimeBy` / `advanceUntilIdle`.
- Wrong timing expectations:
  - Always think in terms of scheduled times; assert only after appropriate advances.
- Not using `backgroundScope` for long-running/fire-and-forget jobs:
  - Infinite or long-lived loops in the main `TestScope` can block `advanceUntilIdle()`.
- Assuming immediate execution:
  - Launching on the test dispatcher may queue work; call `runCurrent()` to flush.

### Immediate Vs Delayed Execution

- `CoroutineStart.UNDISPATCHED` runs the coroutine body immediately up to the first suspension.
- Regular launched coroutines on the test dispatcher are queued and require `runCurrent()` or time advancement to execute.
- Combine with virtual-time primitives so expectations match actual scheduling.

### Best Practices (EN)

1. Use `runTest` with `kotlinx-coroutines-test` for coroutine tests.
2. Use `advanceUntilIdle()` to run all finite scheduled work to completion.
3. Use `advanceTimeBy()` for precise, stepwise time control and intermediate assertions.
4. Use `runCurrent()` to execute tasks scheduled at the current virtual time (including `delay(0)` continuations).
5. Collect `StateFlow`/`SharedFlow` in `backgroundScope` when needed, and cancel collectors explicitly.
6. Describe timing scenarios explicitly with `advanceTimeBy` / `advanceUntilIdle`; do not rely on implicit or real-time waits.

---

## Дополнительные Вопросы (RU)
1. В чём разница между `advanceUntilIdle()` и `advanceTimeBy(``Long``.MAX_VALUE)` при наличии бесконечной или лениво создаваемой работы?
2. Как протестировать бесконечный цикл с `delay()`, не зависая в `advanceUntilIdle()`?
3. Когда стоит использовать `backgroundScope` вместо основного `TestScope` в `runTest`?
4. Как протестировать, что корутина отменяется в определённый момент (например, до завершения `delay`)?
5. Что произойдёт, если вызвать `delay()` вне `TestScope` / без тестового диспетчера, и как это влияет на детерминизм тестов?
6. Как тестировать несколько корутин с разным таймингом, сохраняя детерминированный порядок событий?
7. Можно ли тестировать код без искусственных `delay` с помощью `runTest`, и каковы ограничения такого подхода?
## Follow-ups (EN)
1. What is the difference between `advanceUntilIdle()` and `advanceTimeBy(``Long``.MAX_VALUE)` when there is infinite or lazily produced work?
2. How can you test an infinite loop with `delay()` without hanging in `advanceUntilIdle()`?
3. When should you use `backgroundScope` instead of the main `TestScope` in `runTest`?
4. How can you test that a coroutine is cancelled at a specific moment (e.g., before a delay completes)?
5. What happens if you call `delay()` outside a `TestScope` / without a test dispatcher, and how does this affect test determinism?
6. How can you test multiple coroutines with different timings while keeping the event order deterministic?
7. Can you test code without artificial `delay` using `runTest`, and what are the implications/limitations?
## Ссылки (RU)
- [Kotlin Coroutines Test Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Coroutines Guide](https://developer.android.com/kotlin/coroutines/test)
- [TestScope API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-scope/)
- [Virtual Time in Tests](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md)
- [[c-coroutines]]
- [[c-testing]]
## References (EN)
- [Kotlin Coroutines Test Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Coroutines Guide](https://developer.android.com/kotlin/coroutines/test)
- [TestScope API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-scope/)
- [Virtual Time in Tests](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md)
- [[c-coroutines]]
- [[c-testing]]
## Связанные Вопросы (RU)
- [[q-structured-concurrency-violations--kotlin--hard|Нарушения структурированной конкуренции]]
## Related Questions (EN)
- [[q-structured-concurrency-violations--kotlin--hard|Structured concurrency violations]]