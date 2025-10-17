---
id: "20251015082237201"
title: "Extension Properties / Свойства-расширения"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - extension-functions
  - extensions
  - kotlin
  - programming-languages
  - properties
---
# Свойства какого вида можно добавить как расширение

# Question (EN)
> What kind of properties can be added as extensions?

# Вопрос (RU)
> Свойства какого вида можно добавить как расширение?

---

## Answer (EN)

In Kotlin, you can add extension properties, but only with a custom get (getter). You can add val with get(). Extension properties can only be computed (val) because you cannot create a field inside an extension. var works only with get() and set(), but you still cannot use a field.

---

## Ответ (RU)

В Kotlin можно добавлять свойства-расширения (extension properties), но только с кастомным get (геттером). Можно добавлять val с get(). Расширяемые свойства могут быть только вычисляемыми (val), потому что нельзя создать field внутри расширения. var работает только с get() и set(), но всё равно нельзя использовать field.

