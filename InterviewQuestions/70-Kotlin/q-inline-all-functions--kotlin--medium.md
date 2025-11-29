---
id: lang-069
title: "Inline All Functions / Inline функции"
aliases: [Inline All Functions, Inline functions, Inline функции]
topic: kotlin
subtopics: [kotlin, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin-features, c-performance]
created: 2025-10-15
updated: 2025-11-09
tags: [compiler-optimization, difficulty/medium, inline, inline-functions, kotlin, performance]
date created: Friday, October 31st 2025, 6:31:48 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Можно ли на уровне компилятора сделать все функции inline?

---

# Question (EN)
> Can all functions be made inline at compiler level?

## Ответ (RU)

Нет, компилятор не может (и не должен) делать inline абсолютно все функции.

Ключевые причины:

1. Оптимизации по эвристикам:
   - Решение об inline принимается на основе размера функции, частоты вызовов, ожидаемого выигрыша и роста кода.
   - Глобальное "inline всего" приводит к взрыву размера бинарника и ухудшению кеш-локальности.

2. Ограничения по семантике и информации:
   - Нельзя изменить семантику виртуальных/интерфейсных вызовов и позднего связывания без доказательств конкретного целевого типа; такие вызовы инлайнятся только там, где компилятор может это безопасно определить.
   - Для модульной/инкрементальной компиляции и бинарной совместимости не всегда доступно тело функции во всех местах использования, поэтому inline невозможен.

3. Особые случаи (рекурсия и сложный код):
   - Рекурсивные функции теоретически могут быть частично инлайнинаны, но бесконтрольный inline рекурсии приведет к бесконечному или чрезмерному разворачиванию вызовов, поэтому компилятор обычно этого избегает или ограничивает.
   - Слишком сложные функции (много кода, исключения, сложные ветвления) часто не инлайнятся, потому что выигрыш минимален или отрицателен.

4. Языковые механизмы `inline` (например, в Kotlin):
   - Ключевое слово `inline` — это запрос/подсказка компилятору и механизм генерации байткода (особенно для лямбда-параметров и reified-типов), а не гарантия, что любая произвольная функция будет инлайнинана всегда и везде.
   - Даже при наличии `inline` компилятор может отказаться от инлайнинга в некорректных или неподходящих контекстах.

Вывод: делать "всё inline" на уровне компилятора нельзя и нецелесообразно. Инлайнинг — это локальная оптимизация по эвристикам с учетом семантики, доступности кода и компромисса между скоростью и размером бинарника.

См. также: [[c-kotlin]], [[c-performance]]

## Answer (EN)

No, a compiler cannot (and should not) make all functions inline.

Key reasons:

1. Heuristic-based optimization:
   - Inlining decisions are based on function size, call-site frequency, expected benefit, and code growth.
   - "Inline everything" would cause code bloat and hurt instruction-cache locality.

2. Semantic and visibility constraints:
   - The compiler cannot change the semantics of virtual/interface calls and late binding unless it can prove the concrete target; such calls are inlined only when it is safe.
   - In modular/incremental compilation and for binary compatibility, the compiler often cannot see the function body at all call sites, so it cannot inline them.

3. Special cases (recursion and complex code):
   - Recursive functions can in principle be partially inlined, but unrestricted inlining of recursion would lead to infinite or excessive unrolling, so compilers avoid or strictly limit this.
   - Very large or complex functions (heavy branching, exceptions, etc.) are typically not inlined because the benefit is small or negative.

4. Language-level `inline` mechanisms (e.g., Kotlin):
   - The `inline` keyword is a request/hint and a codegen mechanism (notably for lambda parameters and reified types), not a blanket guarantee that any function can always be inlined everywhere.
   - Even with `inline`, the compiler may refuse to inline in invalid or unsuitable contexts.

Conclusion: making "everything inline" at the compiler level is neither possible nor desirable. Inlining is a local optimization guided by heuristics, semantic safety, code visibility, and trade-offs between speed and binary size.

См. также: [[c-kotlin]], [[c-performance]]

---

## Последующие Вопросы (RU)

- В чем ключевые отличия этого поведения от Java?
- Когда вы бы использовали это на практике?
- Каковы распространенные подводные камни, которых стоит избегать?

## Follow-ups (EN)

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References (EN)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-runtime-generic-access--kotlin--hard]]
- [[q-java-access-modifiers--kotlin--medium]]
