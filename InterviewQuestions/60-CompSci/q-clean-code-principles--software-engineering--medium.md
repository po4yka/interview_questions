---
id: 20251012-600002
title: "Clean Code Principles / Принципы чистого кода"
topic: cs
difficulty: medium
status: draft
created: 2025-10-12
tags: - clean-code
  - best-practices
  - refactoring
  - code-quality
  - readable-code
date_created: 2025-10-12
date_updated: 2025-10-13
moc: moc-cs
related_questions:   - q-solid-principles--software-design--medium
  - q-design-patterns-types--design-patterns--medium
  - q-refactoring-techniques--software-engineering--medium
slug: clean-code-principles-software-engineering-medium
subtopics:   - clean-code
  - software-engineering
  - best-practices
  - code-quality
  - refactoring
---
# Clean Code Principles

## English Version

### Problem Statement

Clean code is code that is easy to understand, easy to maintain, and easy to extend. Following clean code principles improves code quality, reduces bugs, and increases development velocity. Based on Robert C. Martin's (Uncle Bob) "Clean Code" principles.

**The Question:** What are clean code principles? How do you write meaningful names, good functions, and clear comments? What are code smells and how to refactor them?

## Answer (EN)

**Meaningful Names**: Use intention-revealing, pronounceable, and searchable names. Class names should be nouns, and method names should be verbs.
**Functions**: Should be small, do one thing, and have few arguments (ideally 0-2). They should not have side effects, and commands should be separated from queries.
**Comments**: Explain *why*, not *what*. Avoid redundant comments, but use them for TODOs, FIXMEs, and warnings.
**Formatting**: Use consistent vertical and horizontal formatting to improve readability.
**Error Handling**: Use exceptions instead of error codes, and extract `try/catch` blocks into their own functions.
**Code Smells**: Avoid duplicated code, long methods, large classes, and "feature envy" where a method is more interested in another class than its own.

## Ответ (RU)

### ОСМЫСЛЕННЫЕ ИМЕНА

**1. Используйте имена, раскрывающие намерение**

```kotlin
//  Плохо: Что это значит?
val d: Int = 5

//  Хорошо: Ясное намерение
val elapsedTimeInDays: Int = 5
val daysSinceLastUpdate: Int = 5
```

**2. Избегайте дезинформации**

```kotlin
//  Плохо: accountList на самом деле не List
val accountList: Set<Account> = setOf()

//  Хорошо: Используйте точные имена
val accounts: Set<Account> = setOf()
val accountSet: Set<Account> = setOf()
```

**3. Используйте произносимые имена**

```kotlin
//  Плохо: Непроизносимо
data class DtaRcrd102(
    val genymdhms: Long,  // дата генерации, год, месяц, день, час, минута, секунда
    val modymdhms: Long
)

//  Хорошо: Произносимо
data class Customer(
    val generationTimestamp: Long,
    val modificationTimestamp: Long
)
```

**4. Используйте искомые имена**

```kotlin
//  Плохо: Магические числа, трудно искать
for (i in 0 until 34) {
    s += (t[i] * 4) / 5
}

//  Хорошо: Именованные константы
val WORK_DAYS_PER_WEEK = 5
val NUMBER_OF_TASKS = 34
```

**5. Имена классов = существительные, Имена методов = глаголы**

```kotlin
//  Хорошо: Имена классов - существительные
class Customer
class Account

//  Хорошо: Имена методов - глаголы
fun deletePage()
fun save()
```

---

### ФУНКЦИИ

**1. Маленькие функции**

Функции должны быть маленькими. Функции должны быть еще меньше.

**2. Делать одно дело**

Функции должны делать что-то одно. Они должны делать это хорошо. Они должны делать только это.

**3. Мало аргументов (предпочтительно 0-2, избегайте 3+)**

Чем меньше аргументов у функции, тем легче ее понять.

**4. Никаких побочных эффектов**

Функция обещает делать одно дело, но она также делает другие скрытые вещи.

**5. Разделение команд и запросов**

Функция должна либо что-то делать, либо что-то отвечать, но не то и другое вместе.

---

### КОММЕНТАРИИ

**1. Объясняйте почему, а не что**

Не комментируйте плохой код - перепишите его.

**2. Избегайте избыточных комментариев**

Комментарии, которые не добавляют информации, являются избыточными.

**3. Используйте комментарии для TODO, FIXME, WARNING**

`TODO` - это работа, которую нужно сделать, но которую можно отложить. `FIXME` - это проблема, которую нужно исправить. `WARNING` - предостережение о последствиях.

**4. Не комментируйте код - удаляйте его**

Закомментированный код сбивает с толку. Если он вам понадобится, вы можете найти его в системе контроля версий.

---

### ФОРМАТИРОВАНИЕ КОДА

**1. Вертикальное форматирование**

Связанные концепции должны быть расположены близко друг к другу по вертикали.

**2. Горизонтальное форматирование**

Строки не должны быть слишком длинными. 80-120 символов - хороший предел.

---

### ОБРАБОТКА ОШИБОК

**1. Используйте исключения, а не коды ошибок**

Коды ошибок загромождают код и требуют от вызывающей стороны немедленной проверки.

**2. Извлекайте блоки Try/Catch**

Блоки `try/catch` уродливы. Извлекайте их в отдельные функции.

**3. Не возвращайте Null**

Возвращая `null`, вы создаете дополнительную работу для вызывающей стороны.

---

### ЗАПАХИ КОДА (CODE SMELLS)

**1. Дублирование кода**

Повторение - главный враг в программировании.

**2. Длинные методы**

Длинные методы трудно понять и поддерживать.

**3. Большие классы**

Классы, которые делают слишком много, должны быть разделены.

**4. Зависть к функциям (Feature Envy)**

Метод, который больше интересуется другим классом, чем своим собственным.
