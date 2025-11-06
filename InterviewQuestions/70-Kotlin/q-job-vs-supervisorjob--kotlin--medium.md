---
id: kotlin-189
title: "Job Vs Supervisorjob / Job против Supervisorjob"
aliases: ["Job Vs Supervisorjob, Job против Supervisorjob"]
topic: kotlin
subtopics: [access-modifiers]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-job-vs-supervisorjob--kotlin--medium, q-kotlin-final-modifier--programming-languages--easy, q-sam-conversions--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium]
---

# В Чем Отличие Между Job И Supervisor Job

**English**: What is the difference between Job and SupervisorJob?

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

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-final-modifier--programming-languages--easy]]
- [[q-sam-conversions--kotlin--medium]]
- [[q-job-vs-supervisorjob--kotlin--medium]]
