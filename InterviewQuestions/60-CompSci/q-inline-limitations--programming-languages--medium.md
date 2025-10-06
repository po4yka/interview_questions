---
tags:
  - functions
  - inline
  - kotlin
  - programming-languages
difficulty: medium
---

# Бывают ли случаи, когда нельзя использовать inline ?

**English**: Are there cases when you cannot use inline

## Answer

There are situations when using the inline modifier may be unacceptable or impossible. Main cases when inline is undesirable or impossible: 1. Large function code can lead to increased compiled code size. 2. Recursive functions cannot be inlined directly due to infinite loop risk (however, you can inline part of the function using local inline functions for recursive calls). 3. Virtual functions or interface functions cannot be declared as inline due to the need for dynamic resolution. 4. Calls inside inline functions that cannot be inlined will be processed as regular calls, reducing inline efficiency.

## Ответ

Существуют ситуации, когда использование inline модификатора может быть неприемлемым или невозможным. Основные случаи, когда использование inline может быть нежелательным или невозможным: 1. Большой объём кода функции может привести к увеличению размера скомпилированного кода. 2. Рекурсивные функции невозможно встроить напрямую из-за риска бесконечного цикла. Однако можно встроить часть функции с помощью локальных inline функций для рекурсивных вызовов. 3. Виртуальные функции или функции интерфейса не могут быть объявлены как inline из-за необходимости динамического разрешения. 4. Вызовы внутри inline функций, которые не могут быть встроены, будут обрабатываться как обычные вызовы. Это может снизить эффективность использования inline.

