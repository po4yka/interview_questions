---
'---id': kotlin-242
title: Parent-child relationships in structured concurrency / Отношения родитель-дитя
anki_cards:
- slug: q-coroutine-parent-child-relationship-0-en
  language: en
- slug: q-coroutine-parent-child-relationship-0-ru
  language: ru
aliases:
- Parent-Child Relationships
- Отношения родитель-дитя
topic: kotlin
difficulty: medium
original_language: en
language_tags:
- en
- ru
question_kind: theory
status: draft
created: '2025-10-12'
updated: '2025-11-10'
tags:
- coroutines
- difficulty/medium
- hierarchy
- job
- kotlin
- structured-concurrency
description: 'Note stub: to be expanded into a guide on parent-child relationships
  in structured concurrency in Kotlin coroutines'
moc: moc-kotlin
related:
- c-concurrency
- c-coroutines
- c-stateflow
- q-coroutine-performance-optimization--kotlin--hard
- q-retry-operators-flow--kotlin--medium
subtopics:
- coroutines
---
# Вопрос (RU)

> Объясните, как работают отношения родитель-дитя в структурированной конкурентности корутин Kotlin: как формируется иерархия `Job`, как распространяются отмена и исключения между родительскими и дочерними корутинами, как на это влияют различные скоупы (например, `coroutineScope`, `supervisorScope`) и как это отражается на управлении ресурсами и корректности жизненного цикла.

# Question (EN)

> Explain how parent-child relationships work in Kotlin coroutine structured concurrency: how `Job` hierarchies are formed, how cancellation and exceptions propagate between parent and child coroutines, how scopes (e.g., `coroutineScope`, `supervisorScope`) affect this behavior, and how this impacts resource management and lifecycle correctness.

## Ответ (RU)

[Заглушка] Полное решение должно включать с корректными примерами кода:
- Определения: `Job`, `CoroutineScope`, родительские и дочерние корутины, гарантии структурированной конкурентности.
- Как запуск корутин в `CoroutineScope` формирует иерархию `Job`.
- Правила отмены: при отмене родителя отменяются все дочерние корутины; как сбой дочерней корутины влияет на родителя в обычных скоупах.
- Отличия `coroutineScope`/`supervisorScope` и `SupervisorJob` с точки зрения распространения исключений.
- Корректное использование скоупов на уровнях приложения (например, `viewModelScope`, `lifecycleScope`) для избежания утечек.
- Частые ошибки (например, неправильное использование `GlobalScope`) и их влияние на иерархию и отмену.
- Подходы к тестированию иерархий `Job`.
- Ссылки на базовые концепции корутин: [[c-coroutines]].

## Answer (EN)

[Stub] A complete solution should cover, with accurate code examples:
- Definitions: `Job`, `CoroutineScope`, parent and child coroutines, structured concurrency guarantees.
- How launching coroutines in a `CoroutineScope` creates parent-child `Job` hierarchies.
- Cancellation rules: when a parent is cancelled, all its children are cancelled; how child failure affects the parent in regular scopes.
- Differences between `coroutineScope`/`supervisorScope` and `SupervisorJob` regarding exception propagation.
- How to correctly use scopes in application layers (e.g., `viewModelScope`, `lifecycleScope`) to avoid leaks.
- Common mistakes (e.g., using `GlobalScope` incorrectly) and their impact on hierarchy and cancellation.
- Testing patterns related to `Job` hierarchies.
- Reference to core coroutine concepts: [[c-coroutines]].

---

## Дополнительные Вопросы (RU)

1. Опишите, как распространяется отмена в иерархии при использовании `coroutineScope` по сравнению с `supervisorScope`.
2. Объясните разницу между `SupervisorJob` в корневом скоупе и использованием `supervisorScope` вокруг дочерних корутин.
3. Обсудите, как структурированная конкурентность помогает предотвращать утечки корутин в Android/Kotlin-приложениях.
4. Проанализируйте, как следует организовывать обработку исключений в родительских и дочерних корутинах.
5. Покажите распространённые анти-паттерны с использованием `GlobalScope` и то, как они нарушают структурированную конкурентность.

## Follow-ups

1. Describe how cancellation propagates in a hierarchy with `coroutineScope` vs `supervisorScope`, including how failures in one child affect siblings and the parent.
2. Explain the difference between using a `SupervisorJob` at the root scope and wrapping specific child coroutine groups in `supervisorScope` in terms of failure isolation and lifecycle control.
3. Discuss how structured concurrency helps prevent coroutine leaks in Android/Kotlin applications, with examples using `viewModelScope` and `lifecycleScope`.
4. Analyze how exception handling should be structured between parent and child coroutines to ensure proper error reporting without unnecessary cancellation of independent tasks.
5. Show common anti-patterns involving `GlobalScope` (e.g., launching long-lived work from UI components) and explain how they break structured concurrency and complicate cancellation.

---

## Ссылки (RU)

- Официальная документация по Kotlin Coroutines (Job, `CoroutineScope`, структурированная конкурентность).
- Документация по `kotlinx.coroutines` и API `Job`/`CoroutineScope`.

## References

- Kotlin Coroutines official documentation (structured concurrency, Job, CoroutineScope).
- kotlinx.coroutines Job and CoroutineScope API reference.

---

## Связанные Вопросы (RU)

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]
