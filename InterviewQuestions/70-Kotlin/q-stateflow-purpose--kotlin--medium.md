---
---
---\
id: kotlin-158
title: "Stateflow Purpose / Назначение StateFlow"
aliases: [Reactive State, State Management, StateFlow, StateFlow Flow]
topic: kotlin
subtopics: [coroutines, flow, state-management]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2024-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, flow, kotlin, reactive, state-management, stateflow]
---\
# Вопрос (RU)
> Для чего нужен `StateFlow`?

# Question (EN)
> What is `StateFlow` used for?

## Ответ (RU)
`StateFlow` — это специальный вид `Flow` в Kotlin Coroutines, предназначенный для представления и наблюдения всегда доступного состояния.

Основные сценарии использования:
- Экспонирование (передача наружу) состояния UI из `ViewModel` / бизнес-логики
- Реактивное управление состоянием и единый источник правды
- Координация потребителей в корутин-дружественной, типобезопасной форме

Ключевые свойства:
- Горячий поток: его существование не зависит от подписчиков; он всегда хранит значение.
- Всегда имеет начальное значение и запоминает последнее значение.
- Новые коллектора сразу получают текущее значение (повтор последнего состояния).
- Интеграция с Kotlin Coroutines (structured concurrency, отмена, операторы).
- Только для чтения через интерфейс `StateFlow`; изменение выполняется через `MutableStateFlow`.
- Изменение состояния в `MutableStateFlow` через `value` (синхронно) или `emit()` (suspending).
- Во многих Kotlin-only сценариях может заменить `LiveData`, но в отличие от `LiveData` сам по себе не учитывает жизненный цикл.

## Answer (EN)
`StateFlow` is a special kind of `Flow` in Kotlin Coroutines designed for representing and observing a consistently available state.

It is primarily used for:
- Exposing UI state from `ViewModel` / business logic
- Reactive state management and one-source-of-truth state containers
- Coordinating consumers in a coroutine-friendly, type-safe way

Key properties:
- Hot flow: Does not depend on collectors to exist; always holds a value.
- Always has an initial value and keeps the latest value.
- New collectors immediately receive the current value (replay of the last state).
- Integrated with Kotlin Coroutines (structured concurrency, cancellation, operators).
- Read-only interface: `StateFlow` exposes state; mutation is done through `MutableStateFlow`.
- Mutable state via `MutableStateFlow.value` (synchronous) or `emit()` (suspending) when using the mutable variant.
- Suitable replacement for many `LiveData` use cases in Kotlin-only code; unlike `LiveData`, it is not lifecycle-aware by itself.

## Дополнительные Вопросы (RU)

- Чем `StateFlow` отличается от `MutableStateFlow`, `SharedFlow` и `LiveData`?
- Когда вы бы использовали `StateFlow` на практике (например, UI state, конфигурация, кэширование)?
- Какие распространенные ошибки стоит избегать при использовании `StateFlow` (например, использование в Java, учет жизненного цикла, конфляция)?

## Follow-ups

- How does `StateFlow` differ from `MutableStateFlow`, `SharedFlow`, and `LiveData`?
- When would you use `StateFlow` in practice (e.g., UI state, configuration, caching)?
- What are common pitfalls to avoid when using `StateFlow` (e.g., using in Java, lifecycle handling, conflation)?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin по StateFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)

## References

- [[c-kotlin]]
- [Kotlin `StateFlow` Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)

## Связанные Вопросы (RU)

- [[q-kotlin-property-delegates--kotlin--medium]]

## Related Questions

- [[q-kotlin-property-delegates--kotlin--medium]]
