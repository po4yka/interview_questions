---
tags:
  - kotlin
  - programming-languages
  - sealed-classes
difficulty: medium
status: reviewed
---

# В чем особенность sealed классов

**English**: What are the features of sealed classes?

## Answer

The feature of sealed classes is restricting the inheritance hierarchy: all their subclasses must be declared in the same file as the sealed class itself. This makes it an ideal tool for creating restricted class hierarchies where you need strict control over the set of possible subtypes, especially when modeling states or operation results as an inheritance tree.

## Ответ

Особенность запечатанных классов заключается в ограничении иерархии наследования: все их подклассы должны быть объявлены в том же файле что и сам запечатанный класс Это делает его идеальным инструментом для создания ограниченных иерархий классов где требуется строго контролировать набор возможных подтипов особенно при моделировании состояний или результатов операций в виде дерева наследования

