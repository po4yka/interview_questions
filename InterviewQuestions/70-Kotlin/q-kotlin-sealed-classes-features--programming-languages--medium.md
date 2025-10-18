---
id: 20251012-12271111153
title: "Kotlin Sealed Classes Features"
topic: computer-science
difficulty: medium
status: draft
moc: moc-kotlin
related: [q-retrofit-coroutines-best-practices--kotlin--medium, q-testing-stateflow-sharedflow--kotlin--medium, q-kotlin-lambda-expressions--kotlin--medium]
created: 2025-10-15
tags:
  - kotlin
  - programming-languages
  - sealed-classes
---
# В чем особенность sealed классов

# Question (EN)
> What are the features of sealed classes?

# Вопрос (RU)
> В чем особенность sealed классов

---

## Answer (EN)

The feature of sealed classes is restricting the inheritance hierarchy: all their subclasses must be declared in the same file as the sealed class itself. This makes it an ideal tool for creating restricted class hierarchies where you need strict control over the set of possible subtypes, especially when modeling states or operation results as an inheritance tree.

---

## Ответ (RU)

Особенность запечатанных классов заключается в ограничении иерархии наследования: все их подклассы должны быть объявлены в том же файле что и сам запечатанный класс Это делает его идеальным инструментом для создания ограниченных иерархий классов где требуется строго контролировать набор возможных подтипов особенно при моделировании состояний или результатов операций в виде дерева наследования

## Related Questions

- [[q-retrofit-coroutines-best-practices--kotlin--medium]]
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-kotlin-lambda-expressions--kotlin--medium]]
