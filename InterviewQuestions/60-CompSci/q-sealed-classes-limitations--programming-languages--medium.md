---
tags:
  - kotlin
  - sealed-classes
  - class-hierarchy
  - easy_kotlin
  - programming-languages
difficulty: medium
---

# Какие есть ограничения у sealed классов?

**English**: What are the limitations of sealed classes?

## Answer

Sealed class limitations: all subtypes must be defined in the same file, sealed class cannot be an interface or abstract class directly, sealed classes and their subtypes cannot be private, sealed classes don't support inheritance from other classes except Any and can only be used for classes and objects but not interfaces. Sealed classes also provide exhaustive when expressions, full control over class hierarchy, and pattern matching support.

## Ответ

Ограничения sealed классов: все подтипы должны быть определены в том же файле, sealed класс не может быть интерфейсом или абстрактным классом напрямую, sealed классы и их подтипы не могут быть private, sealed классы не поддерживают наследование от других классов кроме Any и могут использоваться только для классов и объектов но не интерфейсов. Также sealed классы обеспечивают исчерпывающие выражения when, полный контроль над иерархией классов и поддержку сопоставления с образцом.

