---
id: android-484
title: "StateFlow vs Flow vs SharedFlow vs LiveData / StateFlow против Flow, SharedFlow и LiveData"
aliases: [SharedFlow и LiveData, StateFlow vs Flow vs SharedFlow vs LiveData, StateFlow против Flow]
topic: android
subtopics: [coroutines, flow, ui-state]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, q-flow-vs-livedata-comparison--kotlin--medium, q-testing-coroutines-flow--android--hard]
created: 2025-10-26
updated: 2025-10-26
tags: [android/coroutines, android/flow, android/ui-state, difficulty/medium, state-management]
sources: [https://developer.android.com/kotlin/flow/stateflow-and-sharedflow, https://developer.android.com/topic/libraries/architecture/livedata]
---

# Вопрос (RU)
> Когда в Android приложении стоит выбирать `StateFlow`, `SharedFlow`, обычный `Flow` или `LiveData` для доставки и наблюдения состояния UI?

# Question (EN)
> When should an Android app expose `StateFlow`, `SharedFlow`, a cold `Flow`, or `LiveData` for delivering and observing UI state?

---

## Ответ (RU)
`StateFlow` и `SharedFlow` являются горячими потоками поверх Kotlin `Flow`, а `LiveData` — компонент архитектуры Android, ориентированный на жизненный цикл. Выбор зависит от типа данных, требуемой семантики подписки, поддержки жизненного цикла и совместимости со стеками (Compose, XML, Java).

### `StateFlow`
- Реплицирует семантику поведения `BehaviorSubject`: всегда хранит последнее значение, моментально выдает его новым подписчикам.
- Идеален для UI-состояния в `ViewModel`, когда нужно одно актуальное значение и последовательность обновлений.
- Поддерживает неизменяемость (экспонируется как `StateFlow<T>`, изменяется через `MutableStateFlow`).

### `SharedFlow`
- Горячий поток без обязательного начального значения, может буферизовать несколько последних эмиссий.
- Подходит для одноразовых событий (навигация, сообщения об ошибках) и широковещательных обновлений нескольким подписчикам.
- Гибко настраивается по буферу, переполнению и повторной доставке.

### `Flow`
- Холодный поток: каждый сбор запускает новый upstream.
- Используйте для запросов к репозиторию, обратимых последовательностей, ленивых вычислений, где каждый наблюдатель должен выполнить работу заново.
- Подходит для одноразового чтения данных, но не для долгого хранения состояния UI.

### `LiveData`
- Осведомлен о жизненном цикле: автоматически отписывает наблюдателей при `onStop`.
- Уместен, если проект на Java или базируется на XML-фрагментах без Compose, и требуется интеграция с `DataBinding`.
- Ограничен только основным потоком и беден в API операторах по сравнению с `Flow`.

#### Правила Выбора
- Нужен последний слепок состояния + поддержка Compose → `StateFlow`.
- Нужны множественные получатели событий или одноразовые триггеры → `SharedFlow`.
- Данные вычисляются по требованию, каждый сбор независим → холодный `Flow`.
- Наследие на Java/XML или требуется жизненный цикл без корутин → `LiveData`.

#### Практические Рекомендации
- Храните мутируемый поток внутри слоя (`private val _state = `MutableStateFlow`(...)`), снаружи отдавайте только read-only интерфейс.
- Конвертируйте `Flow` в `StateFlow` через `stateIn`, если нужно кэшировать последний результат.
- Для `LiveData` в новых слоях используйте адаптеры (`asLiveData()`) только на границе с UI, чтобы остальная часть стека оставалась на `Flow`.

## Answer (EN)
`StateFlow` and `SharedFlow` are hot flows built on Kotlin `Flow`, while `LiveData` is an Android Architecture Component that is lifecycle-aware. The decision rests on data shape, subscription semantics, lifecycle awareness, and compatibility with Compose, XML, or Java.

### `StateFlow`
- Mirrors a `BehaviorSubject`: always keeps the latest value and replays it to newcomers.
- Ideal for `ViewModel` UI state where a single source of truth must emit sequential updates.
- Promotes immutability by exposing `StateFlow<T>` and mutating through an internal `MutableStateFlow`.

### `SharedFlow`
- Hot stream with no mandatory initial value and configurable replay/buffer.
- Suits one-off events (navigation, snackbars) and broadcasting updates to multiple collectors.
- Flexible backpressure knobs for buffer size, overflow strategy, and delivery guarantees.

### `Flow`
- Cold stream: every collection restarts the upstream work.
- Use for repository queries, repeatable computations, and lazy sequences where each observer should redo the work.
- Useful for data loads or transformations, but poor as a long-lived UI state holder.

### `LiveData`
- `Lifecycle`-aware: unsubscribes observers when the lifecycle reaches `onStop`.
- Helpful when the stack is still XML/Java-based and you need tight integration with DataBinding.
- Main-thread only and limited operator surface compared with `Flow`.

#### Decision Rules
- Need the latest UI snapshot with Compose-first UI → `StateFlow`.
- Need multi-consumer events or fire-and-forget signals → `SharedFlow`.
- Need on-demand, independent computations → cold `Flow`.
- Legacy Java/XML or lifecycle handling without coroutines → `LiveData`.

#### Practical Guidance
- Keep the mutable stream private (`private val _state = `MutableStateFlow`(...)`) and expose read-only types outward.
- Convert `Flow` into `StateFlow` via `stateIn` when you must cache the latest emission.
- If `LiveData` is required, adapt at the UI boundary (`asLiveData()`) so the rest of the stack remains `Flow`-based.

## Follow-ups
- How do you migrate an existing `LiveData`-based screen to expose `StateFlow` without breaking observers?
- What strategies help to avoid event duplication when using `SharedFlow` for navigation commands?
- How does `stateIn` compare to `shareIn` when converting repository flows to UI-facing streams?

## References

- [[c-coroutines]]
- https://developer.android.com/kotlin/flow/stateflow-and-sharedflow
- [`LiveData`](https://developer.android.com/topic/libraries/architecture/livedata)


## Related Questions
- [[q-flow-vs-livedata-comparison--kotlin--medium]]
- [[q-testing-coroutines-flow--android--hard]]
