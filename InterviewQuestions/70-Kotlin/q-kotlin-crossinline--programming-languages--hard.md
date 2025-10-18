---
id: 20251012-12271111118
title: "Kotlin Crossinline / crossinline в Kotlin"
topic: computer-science
difficulty: hard
status: draft
created: 2025-10-15
tags:
  - crossinline
  - inline
  - inline-functions
  - kotlin
  - programming-languages
---
# Зачем нужен crossinline?

# Question (EN)
> What is crossinline used for?

# Вопрос (RU)
> Зачем нужен crossinline?

---

## Answer (EN)

The crossinline keyword is used in the context of inline functions and is important for correctly managing lambda expressions passed to these functions as parameters. Inline functions avoid the overhead of function calls and lambda object creation, improving performance in critical scenarios. However, using inline functions has certain limitations and possibilities, including non-inlined lambda calls. crossinline is needed to ensure safety and correctness when passing lambda expressions that shouldn't contain non-local returns (e.g., returns from the outer function) to inline functions. This keyword guarantees that the lambda expression won't use non-local returns, allowing safe lambda inlining even in contexts where non-local returns could lead to unexpected behavior or errors.

---

## Ответ (RU)

Ключевое слово crossinline используется в контексте встроенных функций (inline functions) и имеет важное значение для корректного управления лямбда-выражениями, передаваемыми в эти функции как параметры. Встроенные функции позволяют избежать затрат на вызов функций и создание объектов лямбда-выражений при каждом вызове, что может улучшить производительность кода, особенно в критичных сценариях. Однако использование inline функций влечёт за собой определённые ограничения и возможности, среди которых и возможность "невстроенного" вызова лямбды. Необходим для обеспечения безопасности и корректности программы при передаче лямбда-выражений, которые не должны содержать нелокальных возвратов (например, возвратов из внешней функции), в inline функции. Это ключевое слово гарантирует, что лямбда-выражение не будет использовать нелокальный возврат, что позволяет безопасно встраивать лямбды, даже если они используются в контексте, где нелокальные возвраты могут привести к неожиданному поведению или ошибкам.

