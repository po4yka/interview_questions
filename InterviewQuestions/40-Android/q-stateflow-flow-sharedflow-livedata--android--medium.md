---
id: android-484
title: StateFlow vs Flow vs SharedFlow vs LiveData / StateFlow против Flow, SharedFlow
  и LiveData
aliases:
- SharedFlow и LiveData
- StateFlow vs Flow vs SharedFlow vs LiveData
- StateFlow против Flow
topic: android
subtopics:
- coroutines
- flow
- ui-state
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-coroutines
- q-flow-vs-livedata-comparison--kotlin--medium
- q-testing-coroutines-flow--android--hard
created: 2025-10-26
updated: 2025-11-10
tags:
- android/coroutines
- android/flow
- android/ui-state
- difficulty/medium
- state-management
sources:
- https://developer.android.com/kotlin/flow/stateflow-and-sharedflow
- https://developer.android.com/topic/libraries/architecture/livedata
anki_cards:
- slug: android-484-0-ru
  language: ru
  anki_id: 1768420618689
  synced_at: '2026-01-14 23:56:58.692029'
- slug: android-484-0-en
  language: en
  anki_id: 1768420618658
  synced_at: '2026-01-14 23:56:58.660457'
---
# Вопрос (RU)
> Когда в Android приложении стоит выбирать `StateFlow`, `SharedFlow`, обычный `Flow` или `LiveData` для доставки и наблюдения состояния UI?

# Question (EN)
> When should an Android app expose `StateFlow`, `SharedFlow`, a cold `Flow`, or `LiveData` for delivering and observing UI state?

---

## Ответ (RU)
`StateFlow` и `SharedFlow` являются горячими потоками поверх Kotlin `Flow`, а `LiveData` — компонент архитектуры Android, ориентированный на жизненный цикл. Выбор зависит от типа данных, требуемой семантики подписки, поддержки жизненного цикла и совместимости со стеками (Compose, XML, Java).

### `StateFlow`
- Семантика, похожая на `BehaviorSubject`: всегда хранит последнее значение и немедленно выдает его новым подписчикам, при этом требует ненулевого начального значения и консолидирует быстрые обновления (конфлюентный).
- Идеален для UI-состояния в `ViewModel`, когда нужно одно актуальное значение и последовательность обновлений.
- Поддерживает неизменяемость (экспонируется как `StateFlow<T>`, изменяется через `MutableStateFlow`).
- Сам по себе не привязан к жизненному циклу: в UI (View/Compose) нужно управлять сбором с учетом `Lifecycle` (`repeatOnLifecycle`, `collectAsStateWithLifecycle`).

### `SharedFlow`
- Горячий поток без обязательного начального значения, с настраиваемыми `replay` и буфером.
- Подходит для одноразовых событий (навигация, сообщения об ошибках) и широковещательных обновлений нескольким подписчикам при корректной конфигурации (`replay = 0`, подходящий буфер и стратегия переполнения, чтобы не переизлучать старые событий и явно понимать риск потери событий для поздних подписчиков).
- Гибко настраивается по буферу, стратегиям при переполнении и количеству повторяемых значений, но не реализует классический механизм backpressure.
- Не является жизненно-цикло-осведомленным: сбор в UI также нужно привязывать к `Lifecycle`.

### `Flow`
- Холодный поток: каждый сбор запускает новый upstream.
- Используйте для запросов к репозиторию, повторяемых последовательностей, ленивых вычислений, где каждый наблюдатель должен выполнить работу заново.
- Подходит для одноразового чтения данных и трансформаций, но не для долгого хранения состояния UI.

### `LiveData`
- Осведомлен о жизненном цикле: доставляет значения только активным наблюдателям (жизненный цикл в состоянии как минимум `STARTED`), при этом наблюдатель остается зарегистрирован до уничтожения владельца или явного удаления.
- Уместен, если проект на Java или базируется на XML-фрагментах без Compose, и требуется интеграция с `DataBinding`.
- API ориентирован на основной поток: `setValue` вызывается с main-потока, а `postValue` позволяет публиковать из фоновых потоков; по выразительности операторов уступает `Flow`.

#### Правила Выбора
- Нужен последний слепок состояния + поддержка Compose → `StateFlow` (с коллекцией через lifecycle-aware API).
- Нужны множественные получатели событий или одноразовые триггеры → `SharedFlow` с `replay = 0` и корректной настройкой буфера, осознавая, что поздние подписчики не получат уже отправленные события.
- Данные вычисляются по требованию, каждый сбор независим → холодный `Flow`.
- Наследие на Java/XML или требуется жизненный цикл без корутин → `LiveData`.

#### Практические Рекомендации
- Храните мутируемый поток внутри слоя (`private val _state = MutableStateFlow(...)`), снаружи отдавайте только read-only интерфейс.
- Конвертируйте `Flow` в `StateFlow` через `stateIn`, если нужно кэшировать последний результат.
- Для `LiveData` в новых слоях используйте адаптеры (`asLiveData()`) только на границе с UI, чтобы остальная часть стека оставалась на `Flow`.

## Answer (EN)
`StateFlow` and `SharedFlow` are hot flows built on Kotlin `Flow`, while `LiveData` is an Android Architecture `Component` that is lifecycle-aware. The decision rests on data shape, subscription semantics, lifecycle awareness, and compatibility with Compose, XML, or Java.

### `StateFlow`
- Semantics similar to `BehaviorSubject`: always holds the latest value and instantly replays it to new collectors, but requires a non-null initial value and conflates rapid updates.
- Ideal for `ViewModel` UI state where a single source of truth must emit sequential updates.
- Promotes immutability by exposing `StateFlow<T>` and mutating through an internal `MutableStateFlow`.
- Not lifecycle-aware by itself: in the UI you should collect it with lifecycle-aware APIs (e.g., `repeatOnLifecycle`, `collectAsStateWithLifecycle`).

### `SharedFlow`
- Hot stream with no mandatory initial value and configurable replay and buffer.
- Suits one-off events (navigation, snackbars) and broadcasting updates to multiple collectors when configured correctly (`replay = 0` plus appropriate buffer/overflow strategy to avoid replaying stale events and with clear understanding that late collectors will miss past emissions).
- `Provides` configuration for buffer size, overflow behavior, and replay count, but does not implement classic reactive backpressure.
- Not lifecycle-aware: UI code must tie collection to the `Lifecycle`.

### `Flow`
- Cold stream: every collection restarts the upstream work.
- Use for repository queries, repeatable computations, and lazy sequences where each observer should redo the work.
- Useful for one-off data loads or transformations, but not intended as a long-lived UI state holder.

### `LiveData`
- `Lifecycle`-aware: delivers updates only to active observers (lifecycle at least `STARTED`); observers remain registered until the lifecycle owner is destroyed or they are explicitly removed.
- Helpful when the stack is still XML/Java-based and you need tight integration with DataBinding.
- Designed for main-thread interaction: `setValue` must be called on the main thread, while `postValue` can be called from background threads; has a smaller operator surface compared with `Flow`.

#### Decision Rules
- Need the latest UI snapshot with Compose-first UI → `StateFlow` (collected via lifecycle-aware APIs).
- Need multi-consumer events or fire-and-forget signals → `SharedFlow` with `replay = 0` and proper buffering, being aware that late collectors will not receive past events.
- Need on-demand, independent computations → cold `Flow`.
- Legacy Java/XML or lifecycle handling without coroutines → `LiveData`.

#### Practical Guidance
- Keep the mutable stream private (`private val _state = MutableStateFlow(...)`) and expose read-only types outward.
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
