---
id: 20251003140802
title: Job vs SupervisorJob / Различия между Job и SupervisorJob
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/13
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-coroutines
  - c-error-handling

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, coroutines, job, supervisorjob, error-handling, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between Job and SupervisorJob

# Вопрос (RU)
> В чем отличие между job и supervisor job

---

## Answer (EN)

Job and SupervisorJob are key concepts related to managing the lifecycle of coroutines.

**Job** represents the basic building block for coroutine lifecycle management and allows task cancellation. The main feature of Job is that **an error in one child coroutine will cause cancellation of all other coroutines in this hierarchy**.

**SupervisorJob** works similarly to Job but with a key difference in exception handling. SupervisorJob **allows child coroutines to complete independently**, so a failure in one coroutine will not cause cancellation of the entire hierarchy.

**Key differences:**
- **Exception handling**: Job cancels all children on error, SupervisorJob doesn't
- **Usage**: Job for dependent tasks, SupervisorJob for independent tasks
- **Application**: SupervisorJob useful for UI components where one failed operation shouldn't break others

## Ответ (RU)

Job и SupervisorJob являются ключевыми понятиями, связанными с управлением жизненным циклом сопрограмм (корутин). Job представляет собой базовый строительный блок управления жизненным циклом корутины и позволяет отменять задачи. Основная особенность Job заключается в том, что ошибка в одной из дочерних корутин приведет к отмене всех остальных корутин в этой иерархии. SupervisorJob работает аналогично Job, но с ключевым отличием в обработке исключений. SupervisorJob позволяет дочерним корутинам завершаться независимо, так что сбой в одной корутине не приведет к отмене всей иерархии. Ключевые отличия: обработка исключений, использование и применение.

---

## Follow-ups
- When should you use SupervisorScope vs supervisorJob?
- How to handle exceptions in supervisor hierarchies?
- What is CoroutineExceptionHandler?

## References
- [[c-kotlin-coroutines]]
- [[c-error-handling]]
- [[moc-kotlin]]

## Related Questions
- [[q-coroutine-context-essence--programming-languages--medium]]
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
