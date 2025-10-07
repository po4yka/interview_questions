---
tags:
  - higher-order-functions
  - inline
  - inline-functions
  - kotlin
  - lambda-expressions
  - performance
  - programming-languages
difficulty: medium
status: draft
---

# Что такое inline функции?

**English**: What are inline functions?

## Answer

Inline functions are a special type of function where the function code is embedded at the call site during compilation. This means that calling an inline function doesn't create a new call stack; instead, the compiler copies the function code directly to the call site. This mechanism is especially useful with higher-order functions that take functions as parameters or return them. Purpose: Reduce function call overhead (no additional function calls or stack creation, improving performance), improve performance with lambda expressions (Kotlin uses objects for lambdas/anonymous functions which can burden the garbage collector - inline functions avoid this by inlining the lambdas), enable language-specific features (only inline functions can use reified type parameters, avoiding runtime type erasure limitations and working with types as regular classes).

## Ответ

Inline функции — это специальный тип функций, при компиляции которых код функции встраивается в место её вызова. Это значит, что при вызове inline функции не происходит создание нового стека вызовов; вместо этого компилятор копирует код функции непосредственно в место вызова. Этот механизм особенно полезен при использовании функций высшего порядка, которые принимают функции в качестве параметров или возвращают их в результате. Для чего они нужны: Уменьшение накладных расходов на вызов функций. Поскольку не происходит дополнительных вызовов функций и не создаётся новый стек, использование inline функций может значительно умен. Улучшение производительности при использовании лямбда-выражений. Kotlin использует объекты для представления лямбда-выражений и анонимных функций, что может привести к дополнительной нагрузке на сборщик мусора и память. Inline функции позволяют избежать этого, поскольку лямбды, переданные в inline функции, также инлайнятся. Возможность использования некоторых специфичных возможностей языка. Например, только inline функции могут использовать реифицированные типовые параметры что позволяет избежать ограничений связанных с типовой стиранием во время выполнения и работать с типами как с обычными классами.

