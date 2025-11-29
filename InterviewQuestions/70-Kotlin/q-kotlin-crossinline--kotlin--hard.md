---
id: lang-205
title: "Kotlin crossinline / crossinline в Kotlin"
aliases: ["crossinline в Kotlin", "Kotlin crossinline"]
topic: kotlin
subtopics: [functions]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-object-singleton-companion--kotlin--medium, q-semaphore-rate-limiting--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/hard, kotlin/functions]
date created: Sunday, October 12th 2025, 12:27:48 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Зачем нужен `crossinline`?

# Question (EN)
> What is `crossinline` used for?

---

## Ответ (RU)

Ключевое слово `crossinline` используется для параметров inline-функций, чтобы ограничить поведение передаваемой лямбды, при этом сохраняя возможность её встраивания (inlining).

Ключевые моменты:
- Обычные параметры inline-функций (без модификаторов) позволяют "нелокальные возвраты": простой `return` внутри такой лямбды может завершить не лямбду, а вызывающую функцию.
- Иногда параметр-лямбду нужно вызывать в другом контексте выполнения (например, внутри другой лямбды, внутри анонимного объекта или после преобразований управления потоком), где нелокальный возврат был бы некорректен или запрещён.
- Объявление параметра с модификатором `crossinline`:
  - запрещает нелокальные возвраты из этой лямбды (разрешены только локальные возвраты вида `return@label`),
  - но не отключает inlining (в отличие от `noinline`, который не позволяет встроить лямбду).

Таким образом, `crossinline` используют для того, чтобы:
- гарантировать, что переданная лямбда не будет делать нелокальные возвраты, и
- позволить компилятору безопасно встроить эту лямбду в местах, где нелокальные возвраты могли бы нарушить корректность или быть запрещены.

## Answer (EN)

The `crossinline` keyword is used for parameters of inline functions to restrict how the passed lambda can behave while still allowing it to be inlined.

Key points:
- Inline functions normally allow "non-local returns" from parameters: a bare `return` inside such a lambda can return from the calling function.
- Sometimes we need to call that parameter lambda from a different execution context (e.g., from inside another lambda, inside an anonymous object, or after some control-flow transformation), where a non-local return would be illegal or misleading.
- Marking a parameter as `crossinline`:
  - forbids non-local returns from that lambda (only `return@label` / local returns are allowed),
  - but still keeps it inline (unlike `noinline`, which disables inlining completely).

Therefore, `crossinline` is used to:
- guarantee that the argument lambda cannot use non-local returns, and
- let the compiler safely inline this lambda in contexts where non-local returns would otherwise break correctness or be disallowed.

## Дополнительные Вопросы (RU)

- [[q-semaphore-rate-limiting--kotlin--medium]]
- [[q-object-singleton-companion--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]

## Follow-ups

- [[q-semaphore-rate-limiting--kotlin--medium]]
- [[q-object-singleton-companion--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]

## Related Questions

- [[q-semaphore-rate-limiting--kotlin--medium]]
- [[q-object-singleton-companion--kotlin--medium]]
- [[q-data-class-detailed--kotlin--medium]]
