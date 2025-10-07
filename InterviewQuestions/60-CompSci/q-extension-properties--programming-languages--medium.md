---
tags:
  - extension-functions
  - extensions
  - kotlin
  - programming-languages
  - properties
difficulty: medium
status: draft
---

# Свойства какого вида можно добавить как расширение

**English**: What kind of properties can be added as extensions?

## Answer

In Kotlin, you can add extension properties, but only with a custom get (getter). You can add val with get(). Extension properties can only be computed (val) because you cannot create a field inside an extension. var works only with get() and set(), but you still cannot use a field.

## Ответ

В Kotlin можно добавлять свойства-расширения (extension properties), но только с кастомным get (геттером). Можно добавлять val с get(). Расширяемые свойства могут быть только вычисляемыми (val), потому что нельзя создать field внутри расширения. var работает только с get() и set(), но всё равно нельзя использовать field.

