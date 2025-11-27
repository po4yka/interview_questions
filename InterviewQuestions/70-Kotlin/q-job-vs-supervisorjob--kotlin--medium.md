---
id: kotlin-189
title: "Job Vs Supervisorjob / Job против Supervisorjob"
aliases: ["Job Vs SupervisorJob", "Job против SupervisorJob"]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium]
date created: Sunday, October 12th 2025, 3:43:42 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> В чем отличие между Job и SupervisorJob?

# Question (EN)
> What is the difference between Job and SupervisorJob?

## Ответ (RU)
Job и SupervisorJob являются ключевыми понятиями, связанными с управлением жизненным циклом корутин (см. [[c-coroutines]]).

- Job (например, родительский Job в CoroutineScope) задает иерархию «родитель–потомок». По умолчанию, если одна дочерняя корутина завершается необработанным исключением, ошибка пробрасывается в родительский Job, и родитель отменяет всех своих дочерних корутин. Это означает, что сбой одной корутины приводит к отмене ее «соседей».
- SupervisorJob изменяет распространение ошибок между дочерними корутинами: если одна дочерняя корутина упала, ее ошибка НЕ отменяет сам SupervisorJob и НЕ отменяет другие дочерние корутины. Остальные дети продолжают работать независимо.

Важные уточнения:
- Вниз по иерархии отмена все так же распространяется для обоих: если явно отменить родительский Job или SupervisorJob, все дочерние корутины будут отменены.
- SupervisorJob не игнорирует собственные ошибки или внешнюю отмену; он лишь предотвращает ситуацию, когда сбой одной дочерней корутины отменяет ее «соседей».

Ключевые отличия:
- Обработка исключений между дочерними корутинами:
  - Job: сбой дочерней корутины приводит к отмене родителя и всех других дочерних корутин.
  - SupervisorJob: сбой дочерней корутины не отменяет родителя и другие дочерние корутины.
- Использование:
  - Job: для групп зависимых задач, где ошибка одной должна приводить к отмене остальных.
  - SupervisorJob: для групп логически независимых задач, где сбой одной операции не должен влиять на другие (например, несколько параллельных UI-операций).

## Answer (EN)
Job and SupervisorJob are key concepts related to managing the lifecycle of coroutines (see [[c-coroutines]]).

- A Job (e.g. the parent job in a CoroutineScope using Job) defines a parent-child hierarchy. By default, if one child coroutine fails with an exception that is not handled, the failure is propagated to the parent Job, and the parent cancels all of its children. This means sibling coroutines are cancelled when one fails.
- A SupervisorJob changes this failure propagation between children: if one child fails, its failure does NOT cancel the SupervisorJob itself and does NOT cancel its sibling coroutines. Other children continue running independently.

Important clarifications:
- Cancellation still propagates downwards for both: if the parent Job or SupervisorJob is cancelled explicitly, all children are cancelled.
- SupervisorJob does not ignore its own failure or external cancellation; it only prevents one child’s failure from cancelling its siblings.

Key differences:
- Exception handling between siblings:
  - Job: child failure cancels the parent and all other children.
  - SupervisorJob: child failure does not cancel the parent or siblings.
- Usage:
  - Job: for groups of dependent tasks where one failure should cancel the rest.
  - SupervisorJob: for groups of logically independent tasks where one failure should not affect others (e.g. multiple parallel UI-related operations).

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java-потоков?
- Когда вы бы использовали Job или SupervisorJob на практике?
- Какие распространенные подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java threads?
- When would you use Job or SupervisorJob in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin]("https://kotlinlang.org/docs/home.html")

## References

- [Kotlin Documentation]("https://kotlinlang.org/docs/home.html")

## Связанные Вопросы (RU)

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-android-async-primitives--android--easy]]

## Related Questions

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-android-async-primitives--android--easy]]
